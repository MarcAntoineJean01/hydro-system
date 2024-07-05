class NakamaServerStartup
   begin
      require 'sinatra'
      require "sinatra/base"

      p "require SUCCESS"
   rescue LoadError => error
      p error
      p "failed to load sinatra, installing gems"
      begin
         sinatraInstall = system("gem install sinatra")
         if !sinatraInstall
            raise "GEM sinatra INSTALL FAILED"
         end
         rackupInstall = system("gem install rackup")
         if ! rackupInstall
            raise "GEM rackup INSTALL FAILED"
         end
         pumaInstall = system("gem install puma")
         if !pumaInstall
            raise "GEM puma INSTALL FAILED"
         end
         require 'sinatra'
      rescue => error
         p error
         p "failed to install gems, ask for help"
      rescue LoadError => error
         p error
         p "failed to load sinatra again, try restarting"
      end
   end

   begin
      Sinatra::Base.get '/test_call' do
         '{
         "test_result":true
      }'
      end
      p "created test_call endpoint"

      Sinatra::Base.get '/water_ph' do
         '{
         "value":9.3
      }'
      end
      p "created water_ph endpoint"

      Sinatra::Base.get '/water_temperature' do
         '{
         "value":27
      }'
      end
      p "created water_temperature endpoint"

      Sinatra::Base.get '/water_ec' do
         '{
         "value":11.5
      }'
      end
      p "created water_ec endpoint"

   rescue => error
      p error
      p "failed to create endpoints, ask for help"
   end

end


newStartup = NakamaServerStartup.new()